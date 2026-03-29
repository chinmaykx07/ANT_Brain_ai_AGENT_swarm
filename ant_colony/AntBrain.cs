using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;

public class AntBrain : MonoBehaviour
{
    // Central Complex (CX) - Path Integration Vector
    private Vector2 cxVector = Vector2.zero;

    // Heading and speed
    public float heading = 0f; // radians
    public float speed = 1f;

    // Antennal Tropotaxis parameters
    public float antennaSensitivity = 1f;
    public float steeringFluidity = 0.1f;

    // Mushroom Body (MB) - Sparse Learning
    private Dictionary<(int, string), float> mbWeights = new Dictionary<(int, string), float>();

    // Sensory inputs (to be set by external sensors)
    public float leftPheromone = 0f;
    public float rightPheromone = 0f;
    public float colonyHunger = 0f;

    // State
    public bool isReturning = false;
    public Vector3 nestPosition;

    void Start()
    {
        nestPosition = transform.position; // Assuming start position is nest
    }

    void Update()
    {
        if (isReturning)
        {
            ReturnLogic();
        }
        else
        {
            ExploreLogic();
        }

        // Move the ant
        Move();
    }

    void ExploreLogic()
    {
        // Get antenna positions (assuming forward is transform.forward)
        Vector3 forward = transform.forward;
        Vector3 leftDir = Quaternion.Euler(0, -45, 0) * forward; // Approximate left
        Vector3 rightDir = Quaternion.Euler(0, 45, 0) * forward;

        // In Unity, you'd raycast or sample a pheromone field here
        // For simplicity, assume leftPheromone and rightPheromone are set externally

        // Steering torque
        float steeringTorque = (leftPheromone - rightPheromone) * antennaSensitivity * steeringFluidity;
        heading += steeringTorque;

        // Mushroom Body influence
        string mbAction = GetMBAction();
        if (mbAction == "left") heading -= 0.1f;
        else if (mbAction == "right") heading += 0.1f;
    }

    void ReturnLogic()
    {
        // Use CX Path Integration
        float targetAngle = Mathf.Atan2(-cxVector.y, -cxVector.x);
        float angleDiff = targetAngle - heading;
        angleDiff = Mathf.Repeat(angleDiff + Mathf.PI, 2 * Mathf.PI) - Mathf.PI; // Normalize to [-pi, pi]

        float steeringForce = angleDiff * 0.5f;
        heading += steeringForce;

        // Check if at nest
        if (Vector3.Distance(transform.position, nestPosition) < 1f)
        {
            isReturning = false;
            cxVector = Vector2.zero;
            // Deposit resource, etc.
        }
    }

    void Move()
    {
        // Update position
        Vector3 movement = new Vector3(Mathf.Cos(heading), 0, Mathf.Sin(heading)) * speed * Time.deltaTime;
        transform.position += movement;

        // Update CX vector
        cxVector += new Vector2(movement.x, movement.z);

        // Update rotation
        transform.rotation = Quaternion.Euler(0, heading * Mathf.Rad2Deg, 0);
    }

    string GetMBAction()
    {
        // Sparse projection (simplified)
        string view = $"{leftPheromone:F2},{rightPheromone:F2},{colonyHunger:F2}";
        int hash = view.GetHashCode();
        List<int> activeIndices = new List<int>();
        for (int i = 0; i < 100 && activeIndices.Count < 5; i++)
        {
            if ((hash & (1 << i)) != 0)
            {
                activeIndices.Add(i);
            }
        }

        string[] actions = { "forward", "left", "right" };
        float[] scores = new float[3];
        foreach (int idx in activeIndices)
        {
            for (int j = 0; j < actions.Length; j++)
            {
                var key = (idx, actions[j]);
                if (mbWeights.ContainsKey(key))
                {
                    scores[j] += mbWeights[key];
                }
            }
        }

        int maxIdx = 0;
        for (int i = 1; i < scores.Length; i++)
        {
            if (scores[i] > scores[maxIdx]) maxIdx = i;
        }
        return actions[maxIdx];
    }

    public void LearnSuccess()
    {
        // Hebbian learning
        string view = $"{leftPheromone:F2},{rightPheromone:F2},{colonyHunger:F2}";
        int hash = view.GetHashCode();
        List<int> activeIndices = new List<int>();
        for (int i = 0; i < 100 && activeIndices.Count < 5; i++)
        {
            if ((hash & (1 << i)) != 0)
            {
                activeIndices.Add(i);
            }
        }

        foreach (int idx in activeIndices)
        {
            var key = (idx, "pickup");
            if (!mbWeights.ContainsKey(key)) mbWeights[key] = 0f;
            mbWeights[key] += 0.1f;
        }
    }

    // Call this when picking up resource
    public void PickupResource()
    {
        isReturning = true;
        LearnSuccess();
    }
}